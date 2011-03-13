//
//  TasklistView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "TasklistListView.h"


@interface TasklistView : UIViewController
{
    id target;
    SEL action;
    IBOutlet TasklistListView *listsCtrl;
    IBOutlet UIToolbar *toolbar;
}

- initWithTarget:(id)target action:(SEL)action;

- (IBAction)onDone:(id)sender;

@end
