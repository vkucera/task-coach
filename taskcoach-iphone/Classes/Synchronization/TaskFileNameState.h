//
//  TaskFileNameState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "OneShotItemState.h"

@interface TaskFileNameState : OneShotItemState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
