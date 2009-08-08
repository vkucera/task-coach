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
	NSString *parentId;
	NSInteger taskCount;
	NSInteger level;
	NSMutableArray *children;
}

@property (nonatomic, readonly) NSString *parentId;
@property (nonatomic) NSInteger level;

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status taskCoachId:(NSString *)taskCoachId parentId:(NSString *)parentId;

- (NSInteger)count;

- (void)addChild:(Category *)child;
- (void)finalizeChildren:(NSMutableArray *)categories;

@end
