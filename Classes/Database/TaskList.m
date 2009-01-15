//
//  TaskList.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskList.h"

#import "Database.h"
#import "Statement.h"

#import "Task.h"

#define CACHELENGTH (8 * 3)

NSDate *dateFromStamp(NSNumber *stamp)
{
	// Takes a timestamp (seconds since the Unix Epoch) and returns an autoreleased NSDate object (or nil)
	if (stamp == nil)
		return nil;
	
	return [NSDate dateWithTimeIntervalSince1970:(NSTimeInterval)[stamp intValue]];
}

@implementation TaskList

@synthesize count;

- (void)countCallback:(NSDictionary *)dict
{
	count = [[dict objectForKey:@"total"] intValue];
}

- (void)taskCallback:(NSDictionary *)dict
{
	Task *task = [[Task alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue]
							   startDate:dateFromStamp([dict objectForKey:@"startDate"])
							   dueDate:dateFromStamp([dict objectForKey:@"dueDate"])
						       completionDate:dateFromStamp([dict objectForKey:@"completionDate"])];
	[tasks addObject:task];
	[task release];
}

- initWithView:(NSString *)viewName category:(NSInteger)categoryId
{
	if (self = [super init])
	{
		tasks = [[NSMutableArray alloc] initWithCapacity:CACHELENGTH];
		request = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM %@ WHERE categoryId=%d ORDER BY name LIMIT ?,?", viewName, categoryId]] retain];

		Statement *countReq = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM %@ WHERE categoryId=%d", viewName, categoryId]];
		[countReq execWithTarget:self action:@selector(countCallback:)];
		
		// firstIndex is already initialized to 0
		[self reload];
	}
	
	return self;
}

- (void)dealloc
{
	[tasks release];
	[request release];
	
	[super dealloc];
}

- (void)reload
{
	[tasks removeAllObjects];
	[request bindInteger:firstIndex atIndex:1];
	[request bindInteger:CACHELENGTH atIndex:2];
	[request execWithTarget:self action:@selector(taskCallback:)];
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
