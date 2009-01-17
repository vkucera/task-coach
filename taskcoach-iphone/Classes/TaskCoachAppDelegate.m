//
//  TaskCoachAppDelegate.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright __MyCompanyName__ 2009. All rights reserved.
//

#import "TaskCoachAppDelegate.h"

@implementation TaskCoachAppDelegate

@synthesize window;
@synthesize mainController;

- (void)applicationDidFinishLaunching:(UIApplication *)application
{
	[window addSubview:mainController.view];
    [window makeKeyAndVisible];
}

- (void)dealloc
{
	[mainController release];
    [window release];

    [super dealloc];
}

@end
