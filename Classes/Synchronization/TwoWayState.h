//
//  TwoWayState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface TwoWayState : BaseState <State>
{
	NSInteger newCategoriesCount;
	NSInteger deletedCategoriesCount;
	NSInteger modifiedCategoriesCount;
	NSInteger newTasksCount;
	NSInteger deletedTasksCount;
	NSInteger modifiedTasksCount;
}

@end
