//
//  TaskView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "TaskTableView.h"

@interface TaskView : UIViewController
{
    void (^doneAction)(UIViewController *);
    NSTimer *refreshStatusTimer;

    IBOutlet TaskTableView *taskTableCtrl;
}

- (id)initWithAction:(void (^)(UIViewController *))action;

- (IBAction)onDone:(id)sender;
- (IBAction)onSelectGrouping:(id)sender;

@end
