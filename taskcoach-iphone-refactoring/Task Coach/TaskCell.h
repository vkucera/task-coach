//
//  TaskCell.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;

@interface TaskCell : UITableViewCell
{
    IBOutlet UILabel *mainLabel;
    IBOutlet UILabel *leftLabel;
    IBOutlet UILabel *rightLabel;
    // XXXTODO: image view
}

- (void)setTask:(CDTask *)task;

@end
