//
//  UploadObjectsState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface UploadObjectsState : BaseState <State>
{
	NSInteger categoryCount;
	NSInteger taskCount;
	NSInteger objectCount;

	NSInteger total;
	NSInteger count;
	NSInteger state;
	
	NSMutableArray *objectIds;
	
	NSObject <State> *nextState;
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller nextState:(NSObject <State> *)nextState expectIds:(BOOL)expectIds;

- (void)activated;
- (void)afterActivation;
- (void)onObject:(NSDictionary *)dict;

// "abstract" methods

- (NSString *)categoryWhereClause;
- (NSString *)taskWhereClause;
- (NSString *)tableName;

@end
