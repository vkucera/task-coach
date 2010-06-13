//
//  SplitViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 13/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#if __IPHONE_OS_VERSION_MAX_ALLOWED >= 30200

#import <UIKit/UIKit.h>

#import "CategoryViewController.h"
#import "CategoryTaskViewController.h"

@interface SplitViewController : UISplitViewController <UISplitViewControllerDelegate>
{
	CategoryViewController *categoryCtrl;
	CategoryTaskViewController *taskCtrl;
}

@property (nonatomic, retain) IBOutlet CategoryViewController *categoryCtrl;
@property (nonatomic, retain) IBOutlet CategoryTaskViewController *taskCtrl;

@end

#endif
