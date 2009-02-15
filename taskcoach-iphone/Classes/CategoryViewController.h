//
//  CategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class NavigationController;

@interface CategoryViewController : UITableViewController
{
	NavigationController *navigationController;
	NSMutableArray *categories;
}

@property (nonatomic, assign) IBOutlet NavigationController *navigationController;

- (IBAction)onAddCategory:(UIBarButtonItem *)button;
- (IBAction)onSynchronize:(UIBarButtonItem *)button;

@end
