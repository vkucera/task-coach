//
//  TaskList.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskList.h"

#import "Database.h"
#import "Statement.h"
#import "SubcategoriesSelector.h"

#import "Task.h"

#import "String+Utils.h"

#import "Configuration.h"

@implementation TaskList

@synthesize parent;
@synthesize title;
@synthesize status;

- initWithView:(NSString *)viewName category:(NSInteger)categoryId title:(NSString *)theTitle status:(NSInteger)theStatus parentTask:(NSNumber *)theParent searchWord:(NSString *)searchWord
{
	NSLog(@"TaskList: %d %@", categoryId, theParent);

	if (self = [super init])
	{
		parent = [theParent retain];
		title = [theTitle copy];
		status = theStatus;

		tasks = [[NSMutableArray alloc] init];

		NSMutableArray *where = [[NSMutableArray alloc] initWithCapacity:2];
		NSString *clauses;
		
		if (![Configuration configuration].showCompleted)
		{
			[where addObject:@"completionDate IS NULL"];
		}
		
		if (searchWord)
		{
			filtered = YES;
			NSString *escaped = [searchWord stringByReplacingOccurrencesOfString:@"\"" withString:@"\\\""];
			[where addObject:[NSString stringWithFormat:@"(name LIKE \"%%%@%%\" OR description LIKE \"%%%@%%\")", escaped, escaped]];
		}

		if (parent)
		{
			[where addObject:[NSString stringWithFormat:@"parentId=%d", [parent intValue]]];
		}
		else
		{
			if (categoryId == -1) // All tasks
			{
				[where addObject:@"parentId IS NULL"];
			}
		}

		if (categoryId == -1)
		{
			clauses = [[NSString stringWithFormat:@" WHERE %@", [@" AND " stringByJoiningStrings:where]] retain];
		}
		else
		{
			// GROUP BY id is there because of tasks that have several categories...
			SubcategoriesSelector *sel = [[SubcategoriesSelector alloc] initWithCategory:categoryId];
			[where addObject:[sel clause]];
			[sel release];

			[where addObject:@"id=idTask"];
			clauses = [[NSString stringWithFormat:@", TaskHasCategory WHERE %@ GROUP BY id", [@" AND " stringByJoiningStrings:where]] retain];
		}

		request = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM %@%@ ORDER BY dueDate, name COLLATE CSDIA", viewName, clauses]] retain];

		[where release];

		[self reload];
	}
	
	return self;
}

- (void)dealloc
{
	[parent release];
	[tasks release];
	[title release];
	[request release];
	
	[super dealloc];
}

- (Task *)taskAtIndex:(NSInteger)index
{
	return [tasks objectAtIndex:index];
}

- (NSInteger)count
{
	return [tasks count];
}

- (void)taskCallback:(NSDictionary *)dict
{
	Task *task = [[Task alloc] initWithId:[[dict objectForKey:@"id"] intValue] fileId:[dict objectForKey:@"fileId"] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue]
							  taskCoachId:[dict objectForKey:@"taskCoachId"]
							  description:[dict objectForKey:@"description"]
								startDate:[dict objectForKey:@"startDate"]
								  dueDate:[dict objectForKey:@"dueDate"]
						   completionDate:[dict objectForKey:@"completionDate"]
								 reminder:[dict objectForKey:@"reminder"]
							   dateStatus:status
								 parentId:[dict objectForKey:@"parentId"]];
	[tasks addObject:task];
	[task release];
}

- (void)reload
{
	[tasks removeAllObjects];
	[request execWithTarget:self action:@selector(taskCallback:)];

	// Now, remove all subtasks that have an ancestor in this list.

	NSMutableDictionary *taskIds = [[NSMutableDictionary alloc] initWithCapacity:[tasks count]];
	for (Task *task in tasks)
		[taskIds setObject:task forKey:[NSNumber numberWithInt:task.objectId]];

	while (1)
	{
		BOOL modified = NO;
		
		for (NSNumber *taskId in [taskIds allKeys])
		{
			Task *task = [taskIds objectForKey:taskId];
			if (task && task.parentId)
			{
				if ([taskIds objectForKey:task.parentId])
				{
					[taskIds removeObjectForKey:taskId];
					modified = YES;
				}
			}
		}
		
		if (!modified)
			break;
	}

	NSArray *oldTasks = [NSArray arrayWithArray:tasks];
	[tasks removeAllObjects];

	for (Task *task in oldTasks)
	{
		if ([taskIds objectForKey:[NSNumber numberWithInt:task.objectId]])
			[tasks addObject:task];
	}
}

@end
