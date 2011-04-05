//
//  ImageButton.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface ImageButton : UIImageView
{
    void (^callback)(id);
    BOOL isInside;
}

- (void)setCallback:(void (^)(id))aCallback;

@end
