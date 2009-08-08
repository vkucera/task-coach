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
@synthesize name;
@synthesize status;
@synthesize taskCoachId;

- initWithId:(NSInteger)theId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)tcId
{
	if (self = [super init])
	{
		objectId = theId;
		name = [theName retain];
		status = theStatus;
		taskCoachId = [tcId retain];
	}
	
	return self;
}

- (void)dealloc
{
	[name release];
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
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET name=?, status=?, taskCoachId=? WHERE id=?", [self class]]] retain];
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
	[[self saveStatement] bindInteger:objectId atIndex:4];
}

- (void)bind
{
	[self bindId];
	[[self saveStatement] bindString:name atIndex:1];
	[[self saveStatement] bindInteger:status atIndex:2];
	[[self saveStatement] bindString:taskCoachId atIndex:3];
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
