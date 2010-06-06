//
//  DayHourState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "OneShotItemState.h"

@interface DayHourState : OneShotItemState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
