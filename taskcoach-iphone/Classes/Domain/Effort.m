//
//  Effort.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 22/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "Effort.h"
#import "DateUtils.h"
#import "Statement.h"
#import "Database.h"

static Statement *_saveStatement = nil;

@implementation Effort

- (Task *)task
{
	// XXXTODO
	return nil;
}

- (NSDate *)started
{
	return started;
}

- (void)setStarted:(NSDate *)theDate
{
	started = theDate;
	[self setStatus:STATUS_MODIFIED];
}

- (NSDate *)ended
{
	return ended;
}

- (void)setEnded:(NSDate *)theDate
{
	ended = theDate;
	[self setStatus:STATUS_MODIFIED];
}

- initWithId:(NSInteger)ID fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId started:(NSDate *)_started ended:(NSDate *)_ended taskId:(NSNumber *)_taskId
{
	if (self = [super initWithId:ID fileId:theFileId name:theName status:theStatus taskCoachId:tcId])
	{
		self.started = _started;
		self.ended = _ended;
		taskId = [_taskId retain];
	}
	
	return self;
}

- (void)dealloc
{
	self.started = nil;
	self.ended = nil;
	[taskId release];
	
	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=?, started=?, ended=?, taskId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:8];
}

- (void)bind
{
	[super bind];

	if (started)
		[[self saveStatement] bindString:[[TimeUtils instance] stringFromDate:started] atIndex:5];
	else
		[[self saveStatement] bindNullAtIndex:5];

	if (ended)
		[[self saveStatement] bindString:[[TimeUtils instance] stringFromDate:ended] atIndex:6];
	else
		[[self saveStatement] bindNullAtIndex:6];

	if (taskId)
		[[self saveStatement] bindInteger:[taskId intValue] atIndex:7];
	else
		[[self saveStatement] bindNullAtIndex:7];
}

@end
