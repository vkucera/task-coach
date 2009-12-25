//
//  Task.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Task.h"
#import "Category.h"

#import "Database.h"
#import "Statement.h"

#import "DateUtils.h"

static Statement *_saveStatement = NULL;

@implementation Task

@synthesize description;
@synthesize startDate;
@synthesize dueDate;
@synthesize completionDate;
@synthesize taskStatus;

- initWithId:(NSInteger)theId fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId description:(NSString *)theDescription
   startDate:(NSString *)theStartDate dueDate:(NSString *)theDueDate completionDate:(NSString *)theCompletionDate dateStatus:(NSInteger)dateStatus
{
	if (self = [super initWithId:theId fileId:theFileId name:theName status:theStatus taskCoachId:tcId])
	{
		description = [theDescription retain];
		startDate = [theStartDate retain];
		dueDate = [theDueDate retain];
		completionDate = [theCompletionDate retain];
		
		taskStatus = dateStatus;
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
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=?, description=?, startDate=?, dueDate=?, completionDate=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:9];
}

- (void)bind
{
	[super bind];

	[[self saveStatement] bindString:description atIndex:5];
	[[self saveStatement] bindString:startDate atIndex:6];
	[[self saveStatement] bindString:dueDate atIndex:7];
	[[self saveStatement] bindString:completionDate atIndex:8];
}

- (void)delete
{
	Statement *req = [[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory WHERE idTask=?"];
	[req bindInteger:objectId atIndex:1];
	[req exec];

	[super delete];
}

- (NSInteger)taskStatus
{
	if (completionDate)
		return TASKSTATUS_COMPLETED;

	return taskStatus;
}

- (void)setCompleted:(BOOL)completed
{
	if (completed)
		self.completionDate = [[DateUtils instance] stringFromDate:[NSDate date]];
	else
		self.completionDate = nil;
}

- (void)hasCategoryCallback:(NSDictionary *)dict
{
	hasCat = YES;
}

- (BOOL)hasCategory:(Category *)category
{
	hasCat = NO;
	Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM TaskHasCategory WHERE idTask=? AND idCategory=?"];
	[req bindInteger:objectId atIndex:1];
	[req bindInteger:[category objectId] atIndex:2];
	[req execWithTarget:self action:@selector(hasCategoryCallback:)];
	return hasCat;
}

- (void)removeCategory:(Category *)category
{
	Statement *req = [[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory WHERE idTask=? AND idCategory=?"];
	[req bindInteger:objectId atIndex:1];
	[req bindInteger:[category objectId] atIndex:2];
	[req exec];
	
	[self setStatus:STATUS_MODIFIED];
	[self save];
}

- (void)addCategory:(Category *)category
{
	Statement *req = [[Database connection] statementWithSQL:@"INSERT INTO TaskHasCategory (idTask, idCategory) VALUES (?, ?)"];
	[req bindInteger:objectId atIndex:1];
	[req bindInteger:[category objectId] atIndex:2];
	[req exec];
	
	[self setStatus:STATUS_MODIFIED];
	[self save];
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
