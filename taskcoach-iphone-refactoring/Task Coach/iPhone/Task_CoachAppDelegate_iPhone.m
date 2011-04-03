//
//  Task_CoachAppDelegate_iPhone.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Task_CoachAppDelegate_iPhone.h"

@implementation Task_CoachAppDelegate_iPhone

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
    mainCtrl = [[MainPageView alloc] init];
    [containerCtrl.view addSubview:mainCtrl.view];

    return [super application:application didFinishLaunchingWithOptions:launchOptions];
}

- (void)dealloc
{
    [mainCtrl release];

	[super dealloc];
}

@end
