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

static Statement *_saveStatement = NULL;

@implementation Task

@synthesize description;
@synthesize startDate;
@synthesize dueDate;
@synthesize completionDate;

- initWithId:(NSInteger)theId name:(NSString *)theName status:(NSInteger)theStatus description:(NSString *)theDescription startDate:(NSString *)theStartDate dueDate:(NSString *)theDueDate completionDate:(NSString *)theCompletionDate;
{
	if (self = [super initWithId:theId name:theName status:theStatus])
	{
		description = [theDescription retain];
		startDate = [theStartDate retain];
		dueDate = [theDueDate retain];
		completionDate = [theCompletionDate retain];
	}
	
	return self;
}

- (void)dealloc
{
	[description release];
	[startDate release];
	[dueDate release];
	[completionDate release];

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET name=?, status=?, description=?, startDate=?, dueDate=?, completionDate=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:7];
}

- (void)bind
{
	[super bind];
	[[self saveStatement] bindString:description atIndex:3];
	[[self saveStatement] bindString:startDate atIndex:4];
	[[self saveStatement] bindString:dueDate atIndex:5];
	[[self saveStatement] bindString:completionDate atIndex:6];
}

- (NSInteger)taskStatus
{
	char bf[4096]; // Gros bill :)
	time_t tm;
	time(&tm);
	strftime(bf, 4096, "%Y-%m-%d", localtime(&tm));
	NSString *now = [NSString stringWithUTF8String:bf];
	
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
	char bf[4096];
	time_t tm;
	time(&tm);
	strftime(bf, 4096, "%Y-%m-%d", localtime(&tm));
	self.completionDate = [NSString stringWithUTF8String:bf];
}

// Overridden setters

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
