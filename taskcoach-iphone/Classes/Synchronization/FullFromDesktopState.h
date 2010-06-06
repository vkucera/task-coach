//
//  FullFromDesktopState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "ItemState.h"

@interface FullFromDesktopState : ItemState
{
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
