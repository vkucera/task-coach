//
//  TaskCoachAppDelegate.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright __MyCompanyName__ 2009. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface TaskCoachAppDelegate : NSObject <UIApplicationDelegate>
{
    UIWindow *window;
	UINavigationController *mainController;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet UINavigationController *mainController;

@end

