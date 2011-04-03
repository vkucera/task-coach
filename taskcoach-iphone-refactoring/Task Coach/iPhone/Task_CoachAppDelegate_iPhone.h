//
//  Task_CoachAppDelegate_iPhone.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "Task_CoachAppDelegate.h"
#import "MainPageView.h"

#import "ContainerView.h"

@interface Task_CoachAppDelegate_iPhone : Task_CoachAppDelegate
{
    IBOutlet ContainerView *containerCtrl;
    MainPageView *mainCtrl;
}

@end
