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
#import "CategoriesSelector.h"

#import "Task.h"

#import "String+Utils.h"

#import "Configuration.h"

#define CACHELENGTH (8 * 3)

@implementation TaskList

@synthesize parent;
@synthesize count;
@synthesize title;
@synthesize status;

- (void)countCallback:(NSDictionary *)dict
{
	count = [[dict objectForKey:@"total"] intValue];
}

- (void)taskCallback:(NSDictionary *)dict
{
	Task *task = [[Task alloc] initWithId:[[dict objectForKey:@"id"] intValue] fileId:[dict objectForKey:@"fileId"] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue]
							   taskCoachId:[dict objectForKey:@"taskCoachId"]
							   description:[dict objectForKey:@"description"]
							   startDate:[dict objectForKey:@"startDate"]
							   dueDate:[dict objectForKey:@"dueDate"]
						       completionDate:[dict objectForKey:@"completionDate"]
							   dateStatus:status
							   parentId:[dict objectForKey:@"parentId"]];
	[tasks addObject:task];
	[task release];
}

- initWithView:(NSString *)viewName category:(NSInteger)categoryId title:(NSString *)theTitle status:(NSInteger)theStatus parentTask:(NSNumber *)theParent
{
	if (self = [super init])
	{
		parent = [theParent retain];

		tasks = [[NSMutableArray alloc] initWithCapacity:CACHELENGTH];

		NSMutableArray *where = [[NSMutableArray alloc] initWithCapacity:2];
		
		if (categoryId != -1)
		{
			CategoriesSelector *sel = [[CategoriesSelector alloc] initWithId:categoryId];
			[where addObject:[sel clause]];
			[sel release];
		}

		if (![Configuration configuration].showCompleted)
		{
			[where addObject:@"completionDate IS NULL"];
		}

		if (parent)
		{
			[where addObject:[NSString stringWithFormat:@"parentId=%d", [parent intValue]]];
		}
		else
		{
			[where addObject:@"parentId IS NULL"];
		}

		NSString *req;

		if ([where count])
		{
			req = [NSString stringWithFormat:@"FROM %@ LEFT JOIN TaskHasCategory ON id=idTask WHERE %@", viewName, [@" AND " stringByJoiningStrings:where]];
		}
		else
		{
			req = [NSString stringWithFormat:@"FROM %@ LEFT JOIN TaskHasCategory ON id=idTask", viewName];
		}

		[where release];

		request = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * %@ GROUP BY id ORDER BY name LIMIT ?,?", req]] retain];
		countRequest = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(DISTINCT(id)) AS total %@", req]] retain];

		title = [theTitle copy];
		status = theStatus;

		// firstIndex is already initialized to 0
		[self reload];
	}
	
	return self;
}

- (void)dealloc
{
	[parent release];
	[tasks release];
	[request release];
	[countRequest release];
	[title release];
	
	[super dealloc];
}

- (void)reload
{
	[tasks removeAllObjects];
	[request bindInteger:firstIndex atIndex:1];
	[request bindInteger:CACHELENGTH atIndex:2];
	[request execWithTarget:self action:@selector(taskCallback:)];
	[countRequest execWithTarget:self action:@selector(countCallback:)];
}

- (Task *)taskAtIndex:(NSInteger)index
{
	if (index < firstIndex)
	{
		firstIndex -= CACHELENGTH;
		[self reload];
	}
	else if (index >= firstIndex + CACHELENGTH)
	{
		firstIndex += CACHELENGTH;
		[self reload];
	}
	
	return [tasks objectAtIndex:index - firstIndex];
}

@end
