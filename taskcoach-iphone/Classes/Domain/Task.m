//
//  Task.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Task.h"
#import "Category.h"
#import "Effort.h"

#import "Database.h"
#import "Statement.h"

#import "DateUtils.h"
#import "Configuration.h"

#import "NSDate+Utils.h"

static Statement *_saveStatement = NULL;

@implementation Task

@synthesize description;
@synthesize startDate;
@synthesize dueDate;
@synthesize completionDate;
@synthesize reminder;
@synthesize taskStatus;
@synthesize parentId;

- initWithId:(NSInteger)theId fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId description:(NSString *)theDescription
   startDate:(NSString *)theStartDate dueDate:(NSString *)theDueDate completionDate:(NSString *)theCompletionDate reminder:(NSString *)theReminder dateStatus:(NSInteger)dateStatus
	parentId:(NSNumber *)myParent
{
	if (self = [super initWithId:theId fileId:theFileId name:theName status:theStatus taskCoachId:tcId])
	{
		description = [theDescription retain];
		startDate = [theStartDate retain];
		dueDate = [theDueDate retain];
		completionDate = [theCompletionDate retain];
		reminder = [theReminder retain];
		parentId = [myParent retain];

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
	[reminder release];

	self.parentId = nil;

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=?, description=?, startDate=?, dueDate=?, completionDate=?, reminder=?, parentId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:11];
}

- (void)bind
{
	[super bind];

	[[self saveStatement] bindString:description atIndex:5];
	[[self saveStatement] bindString:startDate atIndex:6];
	[[self saveStatement] bindString:dueDate atIndex:7];
	[[self saveStatement] bindString:completionDate atIndex:8];
	[[self saveStatement] bindString:reminder atIndex:9];

	if (parentId)
		[[self saveStatement] bindInteger:[parentId intValue] atIndex:10];
	else
		[[self saveStatement] bindNullAtIndex:10];
}

- (void)deleteSubtasks:(NSDictionary *)dict
{
	// XXXTODO: delete efforts as well ?
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM TaskHasCategory WHERE idTask=%@", [dict objectForKey:@"id"]]] exec];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM Task WHERE parentId=%@", [dict objectForKey:@"id"]]] execWithTarget:self action:@selector(deleteSubtasks:)];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM Task WHERE id=%@", [dict objectForKey:@"id"]]] exec];
}

- (void)delete
{
	// XXXTODO: delete efforts as well ?
	Statement *req = [[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory WHERE idTask=?"];
	[req bindInteger:objectId atIndex:1];
	[req exec];

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT id FROM Task WHERE parentId=%d", objectId]] execWithTarget:self action:@selector(deleteSubtasks:)];

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
		self.completionDate = [[TimeUtils instance] stringFromDate:[NSDate dateRounded]];
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

- (void)onChildCount:(NSDictionary *)dict
{
	ccount = [[dict objectForKey:@"total"] intValue];
}

- (NSInteger)childrenCount
{
	if ([Configuration configuration].showCompleted)
	{
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(id) AS total FROM Task WHERE parentId=%d", objectId]] execWithTarget:self action:@selector(onChildCount:)];
	}
	else
	{
		[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(id) AS total FROM Task WHERE parentId=%d AND completionDate IS NULL", objectId]] execWithTarget:self action:@selector(onChildCount:)];
	}

	return ccount;
}

- (void)updateEffort:(NSDictionary *)dict
{
	NSDate *ended = nil;
	if ([dict objectForKey:@"ended"])
		ended = [[TimeUtils instance] dateFromString:[dict objectForKey:@"ended"]];

	_effort = [[Effort alloc] initWithId:[[dict objectForKey:@"id"] intValue] fileId:[dict objectForKey:@"fileId"] name:[dict objectForKey:@"name"] status:[[dict objectForKey:@"status"] intValue] taskCoachId:[dict objectForKey:@"taskCoachId"]
								 started:[[TimeUtils instance] dateFromString:[dict objectForKey:@"started"]] ended:ended taskId:[dict objectForKey:@"taskId"]];
}

- (Effort *)currentEffort
{
	_effort = nil;

	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Effort WHERE taskId=%d AND ended IS NULL", objectId]] execWithTarget:self action:@selector(updateEffort:)];

	return [_effort autorelease];
}

- (void)onEffort:(NSDictionary *)dict
{
	NSDate *ended = nil;
	if ([dict objectForKey:@"ended"])
		ended = [[TimeUtils instance] dateFromString:[dict objectForKey:@"ended"]];

	[_efforts addObject:[[[Effort alloc] initWithId:[[dict objectForKey:@"id"] intValue] fileId:[dict objectForKey:@"fileId"] name:[dict objectForKey:@"name"]
											 status:[[dict objectForKey:@"status"] intValue] taskCoachId:[dict objectForKey:@"taskCoachId"]
											started:[[TimeUtils instance] dateFromString:[dict objectForKey:@"started"]]
											  ended:ended
											 taskId:[dict objectForKey:@"taskId"]] autorelease]];
}

- (NSArray *)efforts
{
	_efforts = [[NSMutableArray alloc] init];
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM CurrentEffort WHERE taskId=%d AND status != %d ORDER BY started DESC", objectId, STATUS_DELETED]] execWithTarget:self action:@selector(onEffort:)];
	NSArray *result = [NSArray arrayWithArray:_efforts];
	[_efforts release];
	_efforts = nil;
	return result;
}

- (void)startTracking
{
	// First, stop tracking if applicable. This shouldn't happen though...
	if ([self currentEffort])
		[self stopTracking];

	// And create new effort
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"INSERT INTO Effort (fileId, name, taskId, started) VALUES (%@, \"\", %d, \"%@\")", fileId, objectId, [[TimeUtils instance] stringFromDate:[NSDate date]]]] exec];
}

- (void)stopTracking
{
	Effort *effort = [self currentEffort];
	effort.ended = [NSDate date];
	[effort save];
}

// Overridden setters

// There is no need to mark subtasks deleted. They will be deleted in the FullFromDesktop state of the
// next sync.

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

- (void)setReminder:(NSString *)date
{
	[reminder release];
	reminder = [date retain];
	[self setStatus:STATUS_MODIFIED];
}

@end
