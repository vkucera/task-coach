//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class CDTask;

@interface TaskDetailsController : UIViewController <UITabBarDelegate>
{
	CDTask *task;
	NSInteger tabIndex;

	UITabBar *tabBar;
	UIView *containerView;
	UIViewController *currentCtrl;
}

@property (nonatomic, retain) IBOutlet UITabBar *tabBar;
@property (nonatomic, retain) IBOutlet UIView *containerView;

- initWithTask:(CDTask *)task;
- initWithTask:(CDTask *)task tabIndex:(NSInteger)index;

@end
