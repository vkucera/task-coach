//
//  FullFromDeviceTaskState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "BaseState.h"

@interface FullFromDeviceTaskState : BaseState <State>
{
	NSMutableArray *taskIds;
	NSInteger state;
	NSInteger taskCount;
	NSInteger count;
	NSInteger total;
}

@end
