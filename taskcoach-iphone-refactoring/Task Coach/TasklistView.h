//
//  TasklistView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "TasklistListView.h"


@interface TasklistView : UIViewController <UIAlertViewDelegate>
{
    void (^doneAction)(UIViewController *);

    IBOutlet TasklistListView *listsCtrl;
    IBOutlet UIToolbar *toolbar;
}

- initWithAction:(void (^)(UIViewController *))action;

- (IBAction)onSave:(id)sender;
- (IBAction)onAdd:(id)sender;

@end
