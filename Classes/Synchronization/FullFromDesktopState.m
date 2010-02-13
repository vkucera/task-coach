//
//  FullFromDesktopState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "FullFromDesktopState.h"
#import "EndState.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Category.h"
#import "Task.h"
#import "Effort.h"
#import "String+Utils.h"
#import "DateUtils.h"
#import "i18n.h"

@implementation FullFromDesktopState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller;
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		idMap = [[NSMutableDictionary alloc] initWithCapacity:32];
	}
	
	return self;
}

- (void)activated
{
	myController.label.text = _("Synchronizing...");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskHasCategory WHERE idTask IN (SELECT id FROM Task WHERE fileId=%@)", [Database connection].currentFile]] exec];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskHasCategory WHERE idCategory IN (SELECT id FROM Category WHERE fileId=%@)", [Database connection].currentFile]] exec];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Task WHERE fileId=%@", [Database connection].currentFile]] exec];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Category WHERE fileId=%@", [Database connection].currentFile]] exec];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Effort WHERE fileId=%@", [Database connection].currentFile]] exec];
	
	[myNetwork expect:12];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[idMap release];
	[categoryName release];
	[categoryId release];
	[taskSubject release];
	[taskId release];
	[taskDescription release];
	[taskStart release];
	[taskDue release];
	[taskCompleted release];
	[effortId release];
	[effortSubject release];
	[effortTaskId release];
	[effortStarted release];
	[effortEnded release];
	
	[super dealloc];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

#define INITIAL                              0
#define CATEGORY_NAME_LENGTH                 1
#define CATEGORY_NAME                        2
#define CATEGORY_ID_LENGTH                   3
#define CATEGORY_ID                          4
#define CATEGORY_PARENT_ID_LENGTH            5
#define CATEGORY_PARENT_ID                   6

#define TASK_SUBJECT_LENGTH                  7
#define TASK_SUBJECT                         8
#define TASK_ID_LENGTH                       9
#define TASK_ID                              10
#define TASK_DESCRIPTION_LENGTH              11
#define TASK_DESCRIPTION                     12
#define TASK_DATE_LENGTH_0                   13
#define TASK_DATE_0                          14
#define TASK_DATE_LENGTH_1                   15
#define TASK_DATE_1                          16
#define TASK_DATE_LENGTH_2                   17
#define TASK_DATE_2                          18
#define TASK_PARENT_LENGTH                   19
#define TASK_PARENT                          20
#define TASK_CATEGORY_COUNT                  21
#define TASK_CATEGORY_ID_LENGTH              22
#define TASK_CATEGORY_ID                     23

#define EFFORT_ID_LENGTH                     24
#define EFFORT_ID                            25
#define EFFORT_SUBJECT_LENGTH                26
#define EFFORT_SUBJECT                       27
#define EFFORT_TASKID_LENGTH                 28
#define EFFORT_TASKID                        29
#define EFFORT_STARTED_LENGTH                30
#define EFFORT_STARTED                       31
#define EFFORT_ENDED_LENGTH                  32
#define EFFORT_ENDED                         33

#define GUID_LENGTH                          34
#define GUID                                 35

- (void)onFoundParent:(NSDictionary *)dict
{
	parentLocalId = [[dict objectForKey:@"id"] intValue];
}

- (void)onFoundEffortTask:(NSDictionary *)dict
{
	effortTaskLocalId = [[dict objectForKey:@"id"] intValue];
}

- (void)createEffort
{
	NSNumber *theTaskId = nil;

	if (effortTaskId)
	{
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM Task WHERE taskCoachId=\"%@\"", effortTaskId]] execWithTarget:self action:@selector(onFoundEffortTask:)];
		theTaskId = [NSNumber numberWithInt:effortTaskLocalId];
	}

	NSLog(@"New effort: %@/%@/%@/%@/%@/%@", [Database connection].currentFile, effortSubject, effortId, effortStarted, effortEnded, theTaskId);

	Effort *effort = [[Effort alloc] initWithId:-1 fileId:[Database connection].currentFile name:effortSubject status:STATUS_NONE taskCoachId:effortId started:effortStarted ended:effortEnded taskId:theTaskId];
	[effort save];
	[effort release];
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	switch (state)
	{
		case INITIAL:
			categoryCount = ntohl(*((int32_t *)[data bytes]));
			taskCount = ntohl(*((int32_t *)([data bytes] + 4)));
			effortCount = ntohl(*((int32_t *)([data bytes] + 8)));
			
			total = categoryCount + taskCount;
			controller.progress.progress = 0;
			
			NSLog(@"%d categories, %d tasks", categoryCount, taskCount);
			
			if (categoryCount)
			{
				state = CATEGORY_NAME_LENGTH;
			}
			else if (taskCount)
			{
				state = TASK_SUBJECT_LENGTH;
			}
			else if (effortCount)
			{
				state = EFFORT_ID_LENGTH;
			}
			else
			{
				state = GUID_LENGTH;
			}

			[network expect:4];

			break;
		
		// Categories

		case CATEGORY_NAME_LENGTH:
			state = CATEGORY_NAME;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case CATEGORY_NAME:
			[categoryName release];
			categoryName = [[NSString stringFromUTF8Data:data] retain];
			
			state = CATEGORY_ID_LENGTH;
			[network expect:4];
			
			break;
		case CATEGORY_ID_LENGTH:
			state = CATEGORY_ID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case CATEGORY_ID:
			[categoryId release];
			categoryId = [[NSString stringFromUTF8Data:data]retain];
			state = CATEGORY_PARENT_ID_LENGTH;
			[network expect:4];

			break;
		case CATEGORY_PARENT_ID_LENGTH:
			state = CATEGORY_PARENT_ID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case CATEGORY_PARENT_ID:
		{
			Category *category;

			if ([data length])
				category = [[Category alloc] initWithId:-1 fileId:[Database connection].currentFile name:categoryName status:STATUS_NONE taskCoachId:categoryId parentId:[idMap valueForKey:[NSString stringFromUTF8Data:data]]];
			else
				category = [[Category alloc] initWithId:-1 fileId:[Database connection].currentFile name:categoryName status:STATUS_NONE taskCoachId:categoryId];

			[category save];
			
			[idMap setValue:[NSNumber numberWithInt:category.objectId] forKey:categoryId];

			[category release];

			NSLog(@"Added category %@", categoryName);

			--categoryCount;
			
			++doneCount;
			controller.progress.progress = 1.0 * doneCount / total;
			
			if (categoryCount)
			{
				state = CATEGORY_NAME_LENGTH;
				[network expect:4];
			}
			else
			{
				if (taskCount)
				{
					state = TASK_SUBJECT_LENGTH;
				}
				else if (effortCount)
				{
					state = EFFORT_ID_LENGTH;
				}
				else
				{
					state = GUID_LENGTH;
				}

				[network expect:4];
			}

			[network appendInteger:1];
			
			break;
		}
			
		// Tasks
			
		case TASK_SUBJECT_LENGTH:
			state = TASK_SUBJECT;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case TASK_SUBJECT:
			[taskSubject release];
			taskSubject = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task subject: %@", taskSubject);
			
			state = TASK_ID_LENGTH;
			[network expect:4];

			break;
		case TASK_ID_LENGTH:
			state = TASK_ID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case TASK_ID:
			[taskId release];
			taskId = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task ID: %@", taskId);
			
			state = TASK_DESCRIPTION_LENGTH;
			[network expect:4];
			
			break;
		case TASK_DESCRIPTION_LENGTH:
			state = TASK_DESCRIPTION;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case TASK_DESCRIPTION:
			[taskDescription release];
			taskDescription = [[NSString stringFromUTF8Data:data] retain];
			NSLog(@"Task description: %@", taskDescription);
			
			state = TASK_DATE_LENGTH_0;
			[network expect:4];
			
			break;
		case TASK_DATE_LENGTH_0:
		case TASK_DATE_LENGTH_1:
		case TASK_DATE_LENGTH_2:
			state = state + 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];

			break;
		case TASK_DATE_0:
		case TASK_DATE_1:
		case TASK_DATE_2:
		{
			NSString **pStr;
			
			switch (state)
			{
				case TASK_DATE_0:
					pStr = &taskStart;
					break;
				case TASK_DATE_1:
					pStr = &taskDue;
					break;
				case TASK_DATE_2:
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
		case TASK_PARENT_LENGTH:
		{
			NSInteger length = ntohl(*((int32_t *)[data bytes]));
			
			parentLocalId = -1;
			
			if (length)
			{
				state = TASK_PARENT;
				[network expect:length];
			}
			else
			{
				state = TASK_CATEGORY_COUNT;
				[network expect:4];
			}

			break;
		}
		case TASK_PARENT:
		{
			NSString *tcId = [NSString stringFromUTF8Data:data];
			NSLog(@"Task parent: %@", tcId);

			Statement *req = [[Database connection] statementWithSQL:@"SELECT id FROM Task WHERE taskcoachId=?"];
			[req bindString:tcId atIndex:1];
			[req execWithTarget:self action:@selector(onFoundParent:)];

			assert(parentLocalId != -1);

			state = TASK_CATEGORY_COUNT;
			[network expect:4];
			
			break;
		}
		case TASK_CATEGORY_COUNT:
		{
			taskCategoryCount = ntohl(*((int32_t *)[data bytes]));
			NSLog(@"Task has %d categories.", taskCategoryCount);

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
			
			Task *task;
			if (parentLocalId > 0)
			{
				task = [[Task alloc] initWithId:-1 fileId:[Database connection].currentFile name:taskSubject status:STATUS_NONE taskCoachId:taskId description:taskDescription
											startDate:taskStart dueDate:taskDue completionDate:taskCompleted dateStatus:TASKSTATUS_UNDEFINED
											 parentId:[NSNumber numberWithInt:parentLocalId]];
			}
			else
			{
				task = [[Task alloc] initWithId:-1 fileId:[Database connection].currentFile name:taskSubject status:STATUS_NONE taskCoachId:taskId description:taskDescription
											startDate:taskStart dueDate:taskDue completionDate:taskCompleted dateStatus:TASKSTATUS_UNDEFINED
											 parentId:nil];
			}

			[task save];
			NSLog(@"Added task %@", taskSubject);
			taskLocalId = task.objectId;
			[task release];

			if (taskCategoryCount)
			{
				state = TASK_CATEGORY_ID_LENGTH;
				[network expect:4];
			}
			else
			{
				++doneCount;
				controller.progress.progress = 1.0 * doneCount / total;
				--taskCount;
				
				NSLog(@"Remaining tasks: %d", taskCount);
				
				if (taskCount)
				{
					state = TASK_SUBJECT_LENGTH;
				}
				else if (effortCount)
				{
					state = EFFORT_ID_LENGTH;
				}
				else
				{
					state = GUID_LENGTH;
				}

				[network expect:4];
				[network appendInteger:1];
			}

			break;
		}
		case TASK_CATEGORY_ID_LENGTH:
			state = TASK_CATEGORY_ID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case TASK_CATEGORY_ID:
		{
			Statement *req = [[Database connection] statementWithSQL:@"SELECT id FROM Category WHERE taskCoachId=?"];
			[req bindString:[NSString stringFromUTF8Data:data] atIndex:1];
			[req execWithTarget:self action:@selector(onFoundCategory:)];
			
			--taskCategoryCount;
			
			if (taskCategoryCount)
			{
				state = TASK_CATEGORY_ID_LENGTH;
				[network expect:4];
			}
			else
			{
				++doneCount;
				controller.progress.progress = 1.0 * doneCount / total;
				--taskCount;
				
				NSLog(@"Remaining tasks: %d", taskCount);

				if (taskCount)
				{
					state = TASK_SUBJECT_LENGTH;
				}
				else if (effortCount)
				{
					state = EFFORT_ID_LENGTH;
				}
				else
				{
					state = GUID_LENGTH;
				}

				NSLog(@"EXPECT");
				[network expect:4];
				NSLog(@"/EXPECT");

				NSLog(@"Sending ACK");
				[network appendInteger:1];
			}
			
			break;
		}
		case EFFORT_ID_LENGTH:
			state = EFFORT_ID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case EFFORT_ID:
			[effortId release];
			effortId = [[NSString stringFromUTF8Data:data] retain];
			state = EFFORT_SUBJECT_LENGTH;
			[network expect:4];
			break;
		case EFFORT_SUBJECT_LENGTH:
			state = EFFORT_SUBJECT;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case EFFORT_SUBJECT:
			[effortSubject release];
			effortSubject = [[NSString stringFromUTF8Data:data] retain];
			state = EFFORT_TASKID_LENGTH;
			[network expect:4];
			break;
		case EFFORT_TASKID_LENGTH:
		{
			[effortTaskId release];
			effortTaskId = nil;

			NSInteger length = ntohl(*((int32_t *)[data bytes]));
			if (length)
			{
				state = EFFORT_TASKID;
				[network expect:length];
			}
			else
			{
				state = EFFORT_STARTED_LENGTH;
				[network expect:4];
			}
			break;
		}
		case EFFORT_TASKID:
			effortTaskId = [[NSString stringFromUTF8Data:data] retain];
			state = EFFORT_STARTED_LENGTH;
			[network expect:4];
			break;
		case EFFORT_STARTED_LENGTH:
			// Never null.
			state = EFFORT_STARTED;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case EFFORT_STARTED:
			[effortStarted release];
			effortStarted = [[[TimeUtils instance] dateFromString:[NSString stringFromUTF8Data:data]] retain];
			state = EFFORT_ENDED_LENGTH;
			[network expect:4];
			break;
		case EFFORT_ENDED_LENGTH:
		{
			[effortEnded release];
			effortEnded = nil;
			
			NSInteger length = ntohl(*((int32_t *)[data bytes]));
			
			if (length)
			{
				state = EFFORT_ENDED;
				[network expect:length];
			}
			else
			{
				[self createEffort];
				
				--effortCount;
				++doneCount;
				controller.progress.progress = 1.0 * doneCount / total;

				if (effortCount)
				{
					state = EFFORT_ID_LENGTH;
				}
				else
				{
					state = GUID_LENGTH;
				}

				[network appendInteger:1];
				[network expect:4];
			}
			break;
		}
		case EFFORT_ENDED:
			effortEnded = [[[TimeUtils instance] dateFromString:[NSString stringFromUTF8Data:data]] retain];
			[self createEffort];
			
			--effortCount;
			++doneCount;
			controller.progress.progress = 1.0 * doneCount / total;
			
			if (effortCount)
			{
				state = EFFORT_ID_LENGTH;
			}
			else
			{
				state = GUID_LENGTH;
			}
			
			[network appendInteger:1];
			[network expect:4];
			break;
		case GUID_LENGTH:
			state = GUID;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			
			break;
		case GUID:
		{
			// We don't care any more
			[network appendInteger:1];
			
			controller.state = [EndState stateWithNetwork:network controller:controller];
		}
		default:
			break;
	}
}

- (void)onFoundCategory:(NSDictionary *)dict
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"INSERT INTO TaskHasCategory (idTask, idCategory) VALUES (%d, %d)", taskLocalId, [[dict objectForKey:@"id"] intValue]]];
	[req exec];
}

@end
