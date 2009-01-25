//
//  Task.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Task.h"

#import "Database.h"
#import "Statement.h"

#import "DateUtils.h"

static Statement *_saveStatement = NULL;

@implementation Task

@synthesize category;
@synthesize description;
@synthesize startDate;
@synthesize dueDate;
@synthesize completionDate;

- initWithId:(NSInteger)theId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId description:(NSString *)theDescription
			startDate:(NSString *)theStartDate dueDate:(NSString *)theDueDate completionDate:(NSString *)theCompletionDate
			category:(NSNumber *)theCategory
{
	if (self = [super initWithId:theId name:theName status:theStatus taskCoachId:tcId])
	{
		description = [theDescription retain];
		startDate = [theStartDate retain];
		dueDate = [theDueDate retain];
		completionDate = [theCompletionDate retain];
		category = [theCategory retain];
	}
	
	return self;
}

- (void)dealloc
{
	[description release];
	[startDate release];
	[dueDate release];
	[completionDate release];
	[category release];

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET name=?, status=?, categoryId=?, description=?, startDate=?, dueDate=?, completionDate=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:9];
}

- (void)bind
{
	[super bind];
	if (category)
		[[self saveStatement] bindInteger:[category intValue] atIndex:4];
	else
		[[self saveStatement] bindNullAtIndex:4];
	[[self saveStatement] bindString:description atIndex:5];
	[[self saveStatement] bindString:startDate atIndex:6];
	[[self saveStatement] bindString:dueDate atIndex:7];
	[[self saveStatement] bindString:completionDate atIndex:8];
}

- (NSInteger)taskStatus
{
	NSString *now = [[DateUtils instance] stringFromDate:[NSDate date]];
	
	if (completionDate)
		return TASKSTATUS_COMPLETED;
	
	if (dueDate && ([now compare:dueDate] == NSOrderedDescending))
		return TASKSTATUS_OVERDUE;

	if (dueDate && ([now compare:dueDate] == NSOrderedSame))
		return TASKSTATUS_DUETODAY;
	
	if (startDate)
		return TASKSTATUS_STARTED;
	
	return TASKSTATUS_NOTSTARTED;
}

- (void)setCompleted:(BOOL)completed
{
	if (completed)
		self.completionDate = [[DateUtils instance] stringFromDate:[NSDate date]];
	else
		self.completionDate = nil;
}

// Overridden setters

// setCategory is not there because it can't be changed from the UI.

- (void)setDescription:(NSString *)descr
{
	[description release];
	description = [descr retain];
	[self setStatus:STATUS_MODIFIED];
}

- (void)setStartDate:(NSString *)date
{
	[startDate release];
	startDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

- (void)setDueDate:(NSString *)date
{
	[dueDate release];
	dueDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

- (void)setCompletionDate:(NSString *)date
{
	[completionDate release];
	completionDate = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

@end
