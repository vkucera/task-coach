//
//  TaskCoachAppDelegate.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright Jérôme Laheurte 2009. See COPYING for details.
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

