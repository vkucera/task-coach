//
//  ItemState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/09/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"
#import "Items.h"
#import "ItemParser.h"

#define NOCOUNT -1

@interface ItemState : BaseState
{
	NSInteger count;
	BaseItem *item;
	
	ItemParser *parser;
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller;

- (NSNumber *)countForEntityName:(NSString *)entityName status:(NSInteger)status;

- (void)startWithFormat:(char *)format count:(NSInteger)theCount;
- (void)sendFormat:(char *)format values:(NSArray *)values;
- (void)onNewObject:(NSArray *)value;
- (void)onFinished;

@end
