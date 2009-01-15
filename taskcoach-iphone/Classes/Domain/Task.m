//
//  Task.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Task.h"

@implementation Task

- initWithId:(NSInteger)theId name:(NSString *)theName status:(NSInteger)theStatus startDate:(NSDate *)theStartDate dueDate:(NSDate *)theDueDate completionDate:(NSDate *)theCompletionDate;
{
	if (self = [super initWithId:theId name:theName status:theStatus])
	{
		startDate = [theStartDate retain];
		dueDate = [theDueDate retain];
		completionDate = [theCompletionDate retain];
	}
	
	return self;
}

- (void)dealloc
{
	[startDate release];
	[dueDate release];
	[completionDate release];

	[super dealloc];
}

@end
