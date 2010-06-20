//
//  SplitView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 20/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CategoryViewController;

@interface SplitView : UISplitViewController
{
	CategoryViewController *categoryCtrl;
}

@property (nonatomic, retain) IBOutlet CategoryViewController *categoryCtrl;

@end
