//
//  MainViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>
#import <MessageUI/MFMailComposeViewController.h>

@class CategoryViewController;

@interface MainViewController : UIViewController
#ifdef DEBUG
<UIAccelerometerDelegate, MFMailComposeViewControllerDelegate>
#endif
{
	UIViewController *viewController;
#ifdef DEBUG
	UIAcceleration *lastAccel;
	NSInteger alertState;
#endif
}

@property (nonatomic, assign) IBOutlet UIViewController *viewController;

@end
