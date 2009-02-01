//
//  TwoWayState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface TwoWayState : BaseState <State>
{
	NSInteger newCategoriesCount;
	NSInteger newTasksCount;
	NSInteger deletedTasksCount;
	NSInteger modifiedTasksCount;
}

@end
