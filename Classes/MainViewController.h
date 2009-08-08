//
//  MainViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class CategoryViewController;

@interface MainViewController : UIViewController
{
	UIViewController *viewController;
}

@property (nonatomic, assign) IBOutlet UIViewController *viewController;

@end
