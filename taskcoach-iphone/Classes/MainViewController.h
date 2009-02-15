//
//  MainViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CategoryViewController;

@interface MainViewController : UIViewController
{
	UIViewController *viewController;
}

@property (nonatomic, assign) IBOutlet UIViewController *viewController;

@end
