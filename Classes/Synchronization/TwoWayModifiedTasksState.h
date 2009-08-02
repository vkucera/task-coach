//
//  TwoWayModifiedTasksState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface TwoWayModifiedTasksState : BaseState <State>
{
	NSInteger protocolVersion;
	NSMutableArray *taskCategories;
}

@end
