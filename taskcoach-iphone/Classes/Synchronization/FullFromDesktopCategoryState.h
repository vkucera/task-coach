//
//  FullFromDesktopCategoryState.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "ItemState.h"

@interface FullFromDesktopCategoryState : ItemState
{
	NSFetchRequest *parentReq;
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller;

@end
