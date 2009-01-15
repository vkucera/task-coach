//
//  Task.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Task.h"

@implementation Task

@synthesize startDate;
@synthesize dueDate;
@synthesize completionDate;

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

// Overridden setters

- (void)setStartDate:(NSDate *)date
{
	[startDate release];
	startDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

- (void)setDueDate:(NSDate *)date
{
	[dueDate release];
	dueDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

- (void)setCompletionDate:(NSDate *)date
{
	[completionDate release];
	completionDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

@end
