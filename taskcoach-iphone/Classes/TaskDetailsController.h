//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class Task;

@interface TaskDetailsController : UIViewController <UITabBarDelegate>
{
	Task *task;
	NSInteger tabIndex;

	UITabBar *tabBar;
	UIView *containerView;
	UIViewController *currentCtrl;
}

@property (nonatomic, retain) IBOutlet UITabBar *tabBar;
@property (nonatomic, retain) IBOutlet UIView *containerView;

- initWithTask:(Task *)task;
- initWithTask:(Task *)task tabIndex:(NSInteger)index;

@end
