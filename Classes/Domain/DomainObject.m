//
//  DomainObject.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DomainObject.h"
#import "Database.h"
#import "Statement.h"

static Statement *_saveStatement = NULL;

@implementation DomainObject

@synthesize objectId;
@synthesize fileId;
@synthesize name;
@synthesize status;
@synthesize taskCoachId;

- initWithId:(NSInteger)theId fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId
{
	if (self = [super init])
	{
		objectId = theId;
		fileId = [theFileId retain];
		name = [theName retain];
		status = theStatus;
		taskCoachId = [tcId retain];
	}
	
	return self;
}

- (void)dealloc
{
	[name release];
	[fileId release];
	[taskCoachId release];
	
	[super dealloc];
}

- (void)setStatus:(NSInteger)newStatus
{
	switch (status)
	{
		case STATUS_NONE:
			status = newStatus;
			break;
		case STATUS_MODIFIED:
		case STATUS_NEW:
			if (newStatus == STATUS_DELETED)
				status = newStatus;
			break;
	}
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)delete
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM %@ WHERE id=?", [self class]]];
	[req bindInteger:objectId atIndex:1];
	[req exec];
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:5];
}

- (void)bind
{
	[self bindId];
	if (fileId)
		[[self saveStatement] bindInteger:[fileId intValue] atIndex:1];
	else
		[[self saveStatement] bindNullAtIndex:1];

	[[self saveStatement] bindString:name atIndex:2];
	[[self saveStatement] bindInteger:status atIndex:3];
	[[self saveStatement] bindString:taskCoachId atIndex:4];
}

- (void)save
{
	if (objectId == -1)
	{
		Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"INSERT INTO %@ (name) VALUES ('')", [self class]]];
		[req exec];
		objectId = [[Database connection] lastRowID];
	}

	[self bind];
	[[self saveStatement] exec];
}

// Overriden setters to maintain the status

- (void)setName:(NSString *)newName
{
	if (![newName isEqualToString:name])
	{
		[name release];
		name = [newName retain];

		[self setStatus:STATUS_MODIFIED];
	}
}

@end
