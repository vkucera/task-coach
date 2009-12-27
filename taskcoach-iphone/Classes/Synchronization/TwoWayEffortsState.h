//
//  TwoWayEffortsState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "BaseState.h"

@interface TwoWayEffortsState : BaseState <State>
{
	NSNumber *trackingTask;
}

@end
