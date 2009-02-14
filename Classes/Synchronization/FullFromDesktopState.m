//
//  FullFromDesktopState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "FullFromDesktopState.h"
#import "EndState.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Category.h"
#import "Task.h"
#import "String+Utils.h"

@implementation FullFromDesktopState

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Synchronizing...", @"Synchronizing title");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;

	[[[Database connection] statementWithSQL:@"DELETE FROM Category"] exec];
	[[[Database connection] statementWithSQL:@"DELETE FROM Task"] exec];
	[[[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory"] exec];
	[[[Database connection] statementWithSQL:@"DELETE FROM Meta WHERE name='guid'"] exec];
	
	[myNetwork expect:8];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[categoryName release];
	[taskSubject release];
	[taskId release];
	[taskDescription release];
	[taskStart release];
	[taskDue release];
	[taskCompleted release];
	
	[super dealloc];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	switch (state)
	{
		case 0:
			categoryCount = ntohl(*((int32_t *)[data bytes]));
			taskCount = ntohl(*((int32_t *)([data bytes] + 4)));
			total = categoryCount + taskCount;
			controller.progress.progress = 0;
			
			NSLog(@"%d categories, %d tasks", categoryCount, taskCount);
			
			if (categoryCount)
			{
				state = 1;
			}
			else if (taskCount)
			{
				state = 5;
			}
			else
			{
				state = 20;
			}

			[network expect:4];

			break;
		
		// Categories

		case 1:
			state = 2;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case 2:
			[categoryName release];
			categoryName = [[NSString stringFromUTF8Data:data] retain];
			
			state = 3;
			[network expect:4];
			
			break;
		case 3:
			state = 4;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case 4:
		{
			NSString *categoryId = [NSString stringFromUTF8Data:data];
			
			Category *category = [[Category alloc] initWithId:-1 name:categoryName status:STATUS_NONE taskCoachId:categoryId];
			[category save];
			[category release];

			NSLog(@"Added category %@", categoryName);

			--categoryCount;
			
			++doneCount;
			controller.progress.progress = 1.0 * doneCount / total;
			
			if (categoryCount)
			{
				state = 1;
				[network expect:4];
			}
			else
			{
				if (taskCount)
				{
					state = 5;
				}
				else
				{
					state = 20;
				}

				[network expect:4];
			}

			break;
		}
			
		// Tasks
			
		case 5:
			state = 6;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case 6:
			[taskSubject release];
			taskSubject = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task subject: %@", taskSubject);
			
			state = 7;
			[network expect:4];

			break;
		case 7:
			state = 8;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case 8:
			[taskId release];
			taskId = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task ID: %@", taskId);
			
			state = 9;
			[network expect:4];
			
			break;
		case 9:
			state = 10;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case 10:
			[taskDescription release];
			taskDescription = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task description: %@", taskDescription);
			
			state = 11;
			[network expect:4];
			
			break;
		case 11:
		case 13:
		case 15:
			state = state + 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case 12:
		case 14:
		case 16:
		{
			NSString **pStr;
			
			switch (state)
			{
				case 12:
					pStr = &taskStart;
					break;
				case 14:
					pStr = &taskDue;
					break;
				case 16:
					pStr = &taskCompleted;
					break;
			}

			[*pStr release];
			*pStr = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Date: %@", *pStr);
			
			state = state + 1;
			[network expect:4];

			break;
		}
		case 17:
		{
			taskCategoryCount = ntohl(*((int32_t *)[data bytes]));

			if (![taskStart length])
			{
				[taskStart release];
				taskStart = nil;
			}
			
			if (![taskDue length])
			{
				[taskDue release];
				taskDue = nil;
			}
			
			if (![taskCompleted length])
			{
				[taskCompleted release];
				taskCompleted = nil;
			}
			
			Task *task = [[Task alloc] initWithId:-1 name:taskSubject status:STATUS_NONE taskCoachId:taskId description:taskDescription
										startDate:taskStart dueDate:taskDue completionDate:taskCompleted];
			[task save];
			NSLog(@"Added task %@", taskSubject);
			taskLocalId = task.objectId;
			[task release];

			if (taskCategoryCount)
			{
				state = 18;
			}
			else
			{
				++doneCount;
				controller.progress.progress = 1.0 * doneCount / total;
				--taskCount;
				
				if (taskCount)
				{
					state = 5;
				}
				else
				{
					state = 20;
				}
			}
				
			[network expect:4];

			break;
		}
		case 18:
			state = 19;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case 19:
		{
			Statement *req = [[Database connection] statementWithSQL:@"SELECT id FROM Category WHERE taskCoachId=?"];
			[req bindString:[NSString stringFromUTF8Data:data] atIndex:1];
			[req execWithTarget:self action:@selector(onFoundCategory:)];
			
			--taskCategoryCount;
			
			if (taskCategoryCount)
			{
				state = 18;
			}
			else
			{
				++doneCount;
				controller.progress.progress = 1.0 * doneCount / total;
				--taskCount;
				
				if (taskCount)
				{
					state = 5;
				}
				else
				{
					state = 20;
				}
			}

			[network expect:4];
			
			break;
		}
		case 20:
			state = 21;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case 21:
		{
			NSString *guid = [[NSString stringFromUTF8Data:data] retain];
			Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO Meta (name, value) VALUES (?, ?)"];
			[req bindString:@"guid" atIndex:1];
			[req bindString:guid atIndex:2];
			[req exec];
			[guid release];

			controller.state = [EndState stateWithNetwork:network controller:controller];
		}
		default:
			break;
	}

	controller.progress.progress = 1.0 * doneCount / (categoryCount + taskCount);
}

- (void)onFoundCategory:(NSDictionary *)dict
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"INSERT INTO TaskHasCategory (idTask, idCategory) VALUES (%d, %d)", taskLocalId, [[dict objectForKey:@"id"] intValue]]];
	[req exec];
}

@end
