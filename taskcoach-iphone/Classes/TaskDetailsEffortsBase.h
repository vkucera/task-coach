//
//  TaskDetailsEffortsBase.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;

@interface TaskDetailsEffortsBase : UITableViewController <NSFetchedResultsControllerDelegate>
{
	CDTask *task;
	UIButton *myButton;
	NSFetchedResultsController *results;
	NSTimeInterval totalSpent;
	NSTimer *updater;
}

- initWithTask:(CDTask *)task;
- (void)setTask:(CDTask *)task;

- (void)updateButton:(UIButton *)button;
- (void)onTrack:(UIButton *)button;

- (void)refreshTotal;

@end
