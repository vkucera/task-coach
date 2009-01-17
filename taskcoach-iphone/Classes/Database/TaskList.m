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

#import "String+Utils.h"

#import "Configuration.h"

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
@synthesize title;
@synthesize status;

- (void)countCallback:(NSDictionary *)dict
{
	count = [[dict objectForKey:@"total"] intValue];
}

- (void)taskCallback:(NSDictionary *)dict
{
	Task *task = [[Task alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue]
							   description:[dict objectForKey:@"descfription"]
							   startDate:dateFromStamp([dict objectForKey:@"startDate"])
							   dueDate:dateFromStamp([dict objectForKey:@"dueDate"])
						       completionDate:dateFromStamp([dict objectForKey:@"completionDate"])];
	[tasks addObject:task];
	[task release];
}

- initWithView:(NSString *)viewName category:(NSInteger)categoryId title:(NSString *)theTitle status:(NSInteger)theStatus
{
	if (self = [super init])
	{
		tasks = [[NSMutableArray alloc] initWithCapacity:CACHELENGTH];

		NSMutableArray *where = [[NSMutableArray alloc] initWithCapacity:2];
		
		if (categoryId != -1)
		{
			[where addObject:[NSString stringWithFormat:@"categoryId == %d", categoryId]];
		}

		if (![Configuration configuration].showCompleted)
		{
			[where addObject:@"completionDate IS NULL"];
		}

		NSString *req;

		if ([where count])
		{
			req = [NSString stringWithFormat:@"FROM %@ WHERE %@", viewName, [@" AND " stringByJoiningStrings:where]];
		}
		else
		{
			req = [NSString stringWithFormat:@"FROM %@", viewName];
		}

		[where release];

		request = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * %@ ORDER BY name LIMIT ?,?", req]] retain];
		countRequest = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total %@", req]] retain];

		title = [theTitle copy];
		status = theStatus;

		// firstIndex is already initialized to 0
		[self reload];
	}
	
	return self;
}

- (void)dealloc
{
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
