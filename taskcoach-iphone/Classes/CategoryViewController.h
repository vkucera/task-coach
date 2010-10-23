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
@class SplitView;
@class CDCategory;
@class CategoryTaskViewController;

@interface CategoryViewController : BaseCategoryViewController <BonjourBrowserDelegate, RestorableController, UIPopoverControllerDelegate>
{
	NavigationController *navigationController;
	SplitView *splitCtrl;

	UIBarButtonItem *syncButton;
	UIBarButtonItem *fileButton;
	BOOL wantSync;
	NSInteger currentCategory;
	NSInteger totalCount;

	NSTimer *minuteTimer;

	CategoryTaskViewController *taskCtrl;

	UIPopoverController *popoverCtrl;
	UIToolbar *theToolbar;
}

@property (nonatomic, assign) IBOutlet NavigationController *navigationController;
@property (nonatomic, assign) IBOutlet SplitView *splitCtrl;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *syncButton;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *fileButton;
@property (nonatomic, assign) IBOutlet CategoryTaskViewController *taskCtrl;
@property (nonatomic, assign) IBOutlet UIToolbar *theToolbar;

- (IBAction)onChooseFile:(UIBarButtonItem *)button;
- (IBAction)onAddCategory:(UIBarButtonItem *)button;
- (IBAction)onSynchronize:(UIBarButtonItem *)button;
- (IBAction)onConfigure:(UIBarButtonItem *)button;

- (void)setWantSync;
- (void)selectAll;

@end
