//
//  GUIDState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "OneShotItemState.h"

@interface GUIDState : OneShotItemState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
