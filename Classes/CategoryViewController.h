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

@interface CategoryViewController : BaseCategoryViewController <BonjourBrowserDelegate, RestorableController, NSNetServiceDelegate>
{
	NavigationController *navigationController;
	UIBarButtonItem *syncButton;
	UIBarButtonItem *fileButton;
	BOOL wantSync;
	NSInteger currentCategory;
	NSInteger totalCount;
}

@property (nonatomic, assign) IBOutlet NavigationController *navigationController;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *syncButton;
@property (nonatomic, assign) IBOutlet UIBarButtonItem *fileButton;

- (IBAction)onChooseFile:(UIBarButtonItem *)button;
- (IBAction)onAddCategory:(UIBarButtonItem *)button;
- (IBAction)onSynchronize:(UIBarButtonItem *)button;

- (void)setWantSync;

@end