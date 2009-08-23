//
//  UploadObjectsState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@class Statement;

@interface UploadObjectsState : BaseState <State>
{
	NSInteger categoryCount;
	NSInteger taskCount;
	//NSInteger objectCount;

	NSInteger total;
	NSInteger count;
	NSInteger state;
	
	NSMutableArray *objectIds;
	
	NSObject <State> *nextState;
	Statement *myStatement;
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller nextState:(NSObject <State> *)nextState expectIds:(BOOL)expectIds;

- (void)start:(Statement *)req;

- (void)activated;
- (void)onObject:(NSDictionary *)dict;

// "abstract" methods

- (NSString *)categoryWhereClause;
- (NSString *)taskWhereClause;
- (NSString *)tableName;

@end
