//
//  Category.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "DomainObject.h"

@interface Category : DomainObject
{
	NSNumber *parentId;
	NSInteger taskCount;
	NSInteger level;
	NSMutableArray *children;
}

@property (nonatomic, readonly) NSNumber *parentId;
@property (nonatomic) NSInteger level;

- initWithId:(NSInteger)ID fileId:(NSNumber *)fileId name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId parentId:(NSNumber *)parentId;

- (NSInteger)countForTable:(NSString *)tableName;

- (void)addChild:(Category *)child;
- (void)finalizeChildren:(NSMutableArray *)categories;

- (void)removeAllTasks;

@end
