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

@interface SplitViewController : UISplitViewController <UISplitViewControllerDelegate>
{
	CategoryViewController *categoryCtrl;
}

@property (nonatomic, retain) IBOutlet CategoryViewController *categoryCtrl;

@end

#endif
