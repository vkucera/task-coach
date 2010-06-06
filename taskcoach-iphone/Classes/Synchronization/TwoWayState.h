//
//  TwoWayState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "OneShotItemState.h"

@interface TwoWayState : OneShotItemState
{
	NSInteger totalCount;
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
