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
#import "CategoriesSelector.h"
#import "String+Utils.h"

static Statement *_saveStatement = nil;

@implementation Category

@synthesize parentId;
@synthesize level;

- initWithId:(NSInteger)ID name:(NSString *)theName status:(NSInteger)theStatus taskCoachId:(NSString *)theTaskCoachId parentId:(NSString *)theParentId
{
	if (self = [super initWithId:ID name:theName status:theStatus taskCoachId:theTaskCoachId])
	{
		parentId = [theParentId retain];
		children = [[NSMutableArray alloc] init];
	}
	
	return self;
}

- (void)dealloc
{
	[parentId release];
	[children release];

	[super dealloc];
}

- (Statement *)saveStatement
{
	if (!_saveStatement)
		_saveStatement = [[[Database connection] statementWithSQL:[NSString stringWithFormat:@"UPDATE %@ SET name=?, status=?, taskCoachId=?, parentTaskCoachId=? WHERE id=?", [self class]]] retain];
	return _saveStatement;
}

- (void)bindId
{
	[[self saveStatement] bindInteger:objectId atIndex:5];
}

- (void)bind
{
	[super bind];
	
	[[self saveStatement] bindString:parentId atIndex:4];
}

- (NSInteger)count
{
	NSMutableArray *where = [[NSMutableArray alloc] initWithCapacity:2];
	
	if (![Configuration configuration].showCompleted)
		[where addObject:@"completionDate IS NULL"];

	CategoriesSelector *sel = [[CategoriesSelector alloc] initWithId:objectId];
	[where addObject:[sel clause]];
	[sel release];
	
	[[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT COUNT(*) AS total FROM AllTask LEFT JOIN TaskHasCategory ON id=idTask WHERE %@", [@" AND " stringByJoiningStrings:where]]] execWithTarget:self action:@selector(setCount:)];

	return taskCount;
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

@end
