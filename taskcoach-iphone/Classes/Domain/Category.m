//
//  Category.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "Category.h"
#import "Database.h"
#import "Statement.h"
#import "Configuration.h"
#import "String+Utils.h"

static Statement *_saveStatement = nil;

@implementation Category

@synthesize parentId;
@synthesize level;

- initWithId:(NSInteger)ID fileId:(NSNumber *)theFileId name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)theTaskCoachId parentId:(NSNumber *)theParentId
{
	if (self = [super initWithId:ID fileId:theFileId name:theName status:theStatus taskCoachId:theTaskCoachId])
	{
		parentId = [theParentId retain];
		children = [[NSMutableArray alloc] init];

		[self invalidateCache];

		/*
		[self countForTable:@"NotStartedTask"];
		[self countForTable:@"StartedTask"];
		[self countForTable:@"DueSoonTask"];
		[self countForTable:@"OverdueTask"];
		 */
	}
	
	return self;
}

- (void)dealloc
{
	[parentId release];
	[children release];
	[countCache release];

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET fileId=?, name=?, status=?, taskCoachId=?, parentId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:6];
}

- (void)bind
{
	[super bind];
	
	if (parentId)
		[[self saveStatement] bindInteger:[parentId intValue] atIndex:5];
	else
		[[self saveStatement] bindNullAtIndex:5];
}

- (NSInteger)countForTable:(NSString *)tableName
{
	/*
	NSNumber *count = [countCache objectForKey:tableName];
	if (count)
	{
		taskCount = [count intValue];
	}
	else
	{
		TaskList *list = [[TaskList alloc] initWithView:tableName category:objectId title:@"" status:0 parentTask:nil searchWord:nil];
		taskCount = [list count];
		[list release];

		[countCache setObject:[NSNumber numberWithInt:taskCount] forKey:tableName];
	}

	return taskCount;
	 */
	
	return 0;
}

- (void)setCount:(NSDictionary *)dict
{
	taskCount = [[dict objectForKey:@"total"] intValue];
}

- (void)addChild:(Category *)child
{
	[children addObject:child];
}

- (void)finalizeChildren:(NSMutableArray *)categories
{
	[categories addObject:self];
	[self release];
	
	for (Category *child in children)
	{
		child.level = level + 1;
		[child finalizeChildren:categories];
	}
	
	[children release];
	children = nil;
}

- (void)removeAllTasks
{
	Statement *req = [[Database connection] statementWithSQL:@"DELETE FROM TaskHasCategory WHERE idCategory=?"];
	[req bindInteger:objectId atIndex:1];
	[req exec];
}

- (void)invalidateCache
{
	[countCache release];
	countCache = [[NSMutableDictionary alloc] init];
}

@end
