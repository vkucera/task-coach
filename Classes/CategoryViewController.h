//
//  CategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "BaseCategoryViewController.h"
#import "BonjourBrowser.h"
#import "SyncViewController.h"
#import "PositionStore.h"

@class NavigationController;

@interface CategoryViewController : BaseCategoryViewController <BonjourBrowserDelegate, RestorableController>
{
	NavigationController *navigationController;
	UIBarButtonItem *syncButton;
	BOOL wantSync;
	NSInteger currentCategory;
}

@property (nonatomic, assign) IBOutlet NavigationController *navigationController;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *syncButton;

- (IBAction)onAddCategory:(UIBarButtonItem *)button;
- (IBAction)onSynchronize:(UIBarButtonItem *)button;

- (void)setWantSync;

@end
